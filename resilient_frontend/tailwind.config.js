/** @type {import('tailwindcss').Config} */

import animations from '@midudev/tailwind-animations'

module.exports = {
  content: ["./src/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        'red-500': 'var(--tw-color-red-500, #ef4444)',
        'pink-500': 'var(--tw-color-pink-500, #ec4899)',
        'purple-500': 'var(--tw-color-purple-500, #a855f7)',
        'indigo-500': 'var(--tw-color-indigo-500, #6366f1)',
        'blue-500': 'var(--tw-color-blue-500, #3b82f6)',
        'green-500': 'var(--tw-color-green-500, #10b981)',
        'yellow-500': 'var(--tw-color-yellow-500, #f59e0b)',
        'orange-500': 'var(--tw-color-orange-500, #f97316)',
        'teal-500': 'var(--tw-color-teal-500, #14b8a6)',
        'cyan-500': 'var(--tw-color-cyan-500, #06b6d4)',
        'emerald-500': 'var(--tw-color-emerald-500, #10b981)',
        'lime-500': 'var(--tw-color-lime-500, #84cc16)',
        'amber-500': 'var(--tw-color-amber-500, #f59e0b)',
        'rose-500': 'var(--tw-color-rose-500, #f43f5e)',
        'violet-500': 'var(--tw-color-violet-500, #8b5cf6)',
        'fuchsia-500': 'var(--tw-color-fuchsia-500, #d946ef)',
        'sky-500': 'var(--tw-color-sky-500, #0ea5e9)',
        'gray-500': 'var(--tw-color-gray-500, #6b7280)',
      }
    },
  },
  corePlugins: {    preflight: false,  },
  plugins: [require('@tailwindcss/forms'), animations],
}

