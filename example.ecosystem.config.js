module.exports = {
  apps : [{
    name: 'xbl-web-api',
    script: 'start.sh',
    instances: 1,
    autorestart: true,
    watch: false,
    env: {
      PORT: '5000',
      XBL_EMAIL: 'xboxliveuser@example.com',
      XBL_PASS: 'securepassword69',
      PYTHONUNBUFFERED: 'TRUE',
    },
  }],
};
