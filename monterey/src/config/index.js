const configs = {
  development: {
    apiUrl: 'http://localhost:5001',
    appName: 'Convertible Bond Backtest (Dev)'
  },
  production: {
    apiUrl: 'http://os.convertedbond.cn',
    appName: 'Convertible Bond Backtest'
  }
};

// Get current environment, fallback to development if not set
const env = import.meta.env.VITE_APP_ENV || 'development';

// Export the config for the current environment
export const config = configs[env]; 