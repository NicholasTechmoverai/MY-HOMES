function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }
 
  

let userInfo;

document.addEventListener('DOMContentLoaded', () => {
    const userInfoCookie = getCookie('user_info');
    if (userInfoCookie) {
      try {
        userInfo = JSON.parse(decodeURIComponent(userInfoCookie));
      } catch (e) {
        console.error('Invalid user_info cookie:', e);
        return;
      }
  
      if (userInfo) {
        document.querySelectorAll('.login-btn').forEach(bt => {
          bt.style.display = 'none';
        });
        console.log("userINfo::",userInfo)
        document.querySelectorAll('.profile-btn').forEach(bt => {
          bt.style.display = 'flex';
          const img = bt.querySelector('img');
          if (img) {
            img.src = userInfo.picture || '/default-profile.png';
          }
        });
      }
    }
  });
  