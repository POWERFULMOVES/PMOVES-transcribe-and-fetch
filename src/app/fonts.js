import localFont from 'next/font/local'

import { Permanent_Marker } from 'next/font/google'



// Keep the Google font as fallback

export const permanentMarker = Permanent_Marker({

  weight: '400',

  subsets: ['latin'],

  display: 'swap',

})



// Add F-Zero SNES font

export const fZeroFont = localFont({

  src: [

    {

      path: '../../public/fonts/F-ZeroSNES.otf',

      weight: '400',

      style: 'normal',

    }

  ],

  variable: '--font-fzero'

}) 
