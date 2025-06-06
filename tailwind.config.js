// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      './templates/**/*.html',   // Catches templates in project root (if any)
      './*/templates/**/*.html', // <--- MOST IMPORTANT: Catches templates inside your apps (league, theme)
                                 // This pattern means "look inside any folder, then 'templates', then any HTML file"
    ],
    theme: {
      extend: {},
    },
    plugins: [
      // Ensure any plugins you need are here, and no problematic ones.
    ],
  }