/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './weather/templates/*.html',
    './weather/templates/registration/*.html',
    './weather/static/js/*.js',
    './weather/static/css/*.css'
  ],
  theme: {
    extend: {
      screens: {
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
      backgroundImage: {
        'radial-1': 'radial-gradient(circle, skyblue, lightcyan, lightblue)',
        'radial-2': 'radial-gradient(circle at 50% 50%, skyblue, lightcyan, lightblue)',
        'radial-3': 'radial-gradient(circle at 25% 25%, skyblue, lightcyan, lightblue)',
      },
    },
  },
  plugins: [],
  variants: {
    extend: {
      //backgroundImage: ['dark'],
    },
  },
  arbitraryValues: {
    width: true,
    height: true,
  },
};
