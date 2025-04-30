function fetchProperties(
    filterType = null,
    max_price = null,
    min_price = null,
    city = null,
    property_type = null,
    bedrooms = null,
    bathrooms = null,
    min_year = null,
    max_year = null,
    owner_id = null,
    property_id = null
  ) {
    const propertyContainer = document.querySelector('.property-container');
    propertyContainer.innerHTML = `
      <div class="loading-spinner">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Loading properties...</p>
      </div>
    `;
  
    // Create payload object with all filters
    const requestBody = {
      type: filterType,
      max_price,
      min_price,
      city,
      property_type,
      bedrooms,
      bathrooms,
      min_year,
      max_year,
      owner_id,
      property_id
    };
  
    fetch('/fetchproperties_special', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          renderProperties(data.properties, data.meta);
          updateFilterButtons(filterType);
        } else {
          showErrorMessage(data.error || 'Failed to load properties');
        }
      })
      .catch(error => {
        console.error('Fetch error:', error);
        showErrorMessage('An error occurred while fetching properties');
        propertyContainer.innerHTML = `
          <div class="error-state">
            <i class="fas fa-exclamation-triangle"></i>
            <p>Failed to load properties. Please try again later.</p>
            <button onclick="fetchProperties()" class="retry-btn">Retry</button>
          </div>
        `;
      });
  }
  
function renderProperties(properties, meta) {
    const propertyContainer = document.querySelector('.property-container');
    
    if (!properties || properties.length === 0) {
        propertyContainer.innerHTML = `
            <div class="no-properties">
                <i class="fas fa-home"></i>
                <h3>No Properties Found</h3>
                <p>We couldn't find any properties matching your criteria.</p>
                <button onclick="clearFilters()" class="clear-filters-btn">Clear Filters</button>
            </div>
        `;
        return;
    }

    propertyContainer.innerHTML = '';
    
    properties.forEach(property => {
        const propertyCard = document.createElement('div');
        propertyCard.classList.add('property-card');
        propertyCard.dataset.id = property.property_id;
        propertyCard.dataset.type = property.property_type;
        propertyCard.dataset.price = property.price;
        
        // Format price with commas
        const formattedPrice = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(property.price).replace('.00', '');
        
        // Get first image or placeholder
        const mainImage = property.featured_image || 
                         (property.images.length > 0 ? property.images[0].url : 
                         'https://images.unsplash.com/photo-1564013799919-ab600027ffc6');
        
        // Create amenities list
        const amenitiesList = property.amenities && property.amenities.length > 0
            ? property.amenities.map(amenity => 
                `<li class="amenity-item">
                    <i class="fas fa-check"></i>
                    <span>${amenity}</span>
                </li>`
              ).join('')
            : '<li class="no-amenities">No amenities listed</li>';
        
        // Calculate age of listing
        const listingDate = new Date(property.listing_date);
        const daysAgo = Math.floor((new Date() - listingDate) / (1000 * 60 * 60 * 24));
        
        propertyCard.innerHTML = `
            <div class="property-image-container">
                <img src="${mainImage}" alt="${property.title}" class="property-image">
                <div class="property-badges">
                    <span class="type-badge ${property.property_type}">${property.property_type}</span>
                    ${property.is_for_rent ? '<span class="status-badge rent">For Rent</span>' : '<span class="status-badge sale">For Sale</span>'}
                    ${daysAgo < 7 ? '<span class="new-badge">New</span>' : ''}
                </div>
                <button class="favorite-btn" onclick="toggleFavorite(this, ${property.property_id})">
                    <i class="far fa-heart"></i>
                </button>
            </div>
            
            <div class="property-details">
                <div class="price-section">
                    <h3 class="property-price">${formattedPrice}</h3>
                    ${property.is_for_rent ? '<span class="price-period">/month</span>' : ''}
                </div>
                
                <h4 class="property-title">${property.title}</h4>
                
                <div class="property-location">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>${property.address}, ${property.city}</span>
                </div>
                
                <div class="property-features">
                    <div class="feature">
                        <i class="fas fa-bed"></i>
                        <span>${property.bedrooms} ${property.bedrooms === 1 ? 'Bed' : 'Beds'}</span>
                    </div>
                    <div class="feature">
                        <i class="fas fa-bath"></i>
                        <span>${property.bathrooms} ${property.bathrooms === 1 ? 'Bath' : 'Baths'}</span>
                    </div>
                    <div class="feature">
                        <i class="fas fa-ruler-combined"></i>
                        <span>${property.size_sqft.toLocaleString()} sqft</span>
                    </div>
                </div>
                
                <div class="property-amenities">
                    <h5>Key Features</h5>
                    <ul class="amenities-list">
                        ${amenitiesList}
                    </ul>
                </div>
                
                <div class="property-footer">
                    <span class="listing-date">
                        <i class="far fa-clock"></i>
                        Listed ${daysAgo === 0 ? 'today' : `${daysAgo} day${daysAgo === 1 ? '' : 's'} ago`}
                    </span>
                    <a href="/property/${property.property_id}" style="text-decoration:none;">
                        <button class="view-details-btn">
                            View Details <i class="fas fa-arrow-right"></i>
                        </button>
                    </a>
                </div>
            </div>
        `;
        
        // Add image gallery hover effect
        const imageContainer = propertyCard.querySelector('.property-image-container');
        if (property.images.length > 1) {
            imageContainer.classList.add('has-multiple-images');
            imageContainer.setAttribute('title', `${property.images.length} photos available`);
        }
        
        propertyContainer.appendChild(propertyCard);
    });
    
    // Add pagination if meta data exists
    if (meta) {
        renderPagination(meta);
    }
}

// Helper functions
function updateFilterButtons(activeFilter) {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.filter === activeFilter) {
            btn.classList.add('active');
        }
    });
}

function renderPagination(meta) {
    const paginationContainer = document.querySelector('.pagination-container');
    if (!meta || meta.total <= meta.limit) {
        paginationContainer.innerHTML = '';
        return;
    }
    
    const totalPages = Math.ceil(meta.total / meta.limit);
    const currentPage = Math.floor(meta.offset / meta.limit) + 1;
    
    let paginationHTML = `
        <div class="pagination">
            <button class="page-btn ${currentPage === 1 ? 'disabled' : ''}" 
                onclick="fetchProperties(null, ${meta.limit}, ${meta.offset - meta.limit})">
                <i class="fas fa-chevron-left"></i> Prev
            </button>
    `;
    
    // Show page numbers
    for (let i = 1; i <= totalPages; i++) {
        paginationHTML += `
            <button class="page-btn ${i === currentPage ? 'active' : ''}" 
                onclick="fetchProperties(null, ${meta.limit}, ${(i - 1) * meta.limit})">
                ${i}
            </button>
        `;
    }
    
    paginationHTML += `
            <button class="page-btn ${currentPage === totalPages ? 'disabled' : ''}" 
                onclick="fetchProperties(null, ${meta.limit}, ${meta.offset + meta.limit})">
                Next <i class="fas fa-chevron-right"></i>
            </button>
        </div>
        <div class="pagination-info">
            Showing ${meta.returned} of ${meta.total} properties
        </div>
    `;
    
    paginationContainer.innerHTML = paginationHTML;
}

function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
    `;
    
    document.querySelector('.property-container').prepend(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    const typeEl = document.getElementById('this-type');

    if (typeEl) {
        const type = typeEl.value || typeEl.textContent || typeEl.innerText;
    
        if (type === 'rent') {
            fetchProperties('rent');
        } else if (type === 'sale') {
            fetchProperties('sale');
        }else if(type === 'profile'){
            const owener_id = viewFields.email.getAttribute('user_id');
            fetchProperties(null,null,null,null,null, null, null, null, null, owener_id, null)
        } else {
            fetchProperties();
        }
    } else {
        fetchProperties();
    }
    
    // Add event listeners for filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            fetchProperties(this.dataset.filter);
        });
    });
});

