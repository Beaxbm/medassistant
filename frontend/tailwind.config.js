/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    // if you use shadcn/ui primitives:
    "./node_modules/@primitives/shadcn-ui/dist/**/*.js"
  ],
  theme: {
    extend: {
      // Add any custom theme values here, e.g. colors, spacing, etc.
    },
  },
  plugins: [
    // Add Tailwind plugins here, e.g. forms, typography, etc.
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/typography'),
  ],
};
