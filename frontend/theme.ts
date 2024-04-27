'use client';
import { experimental_extendTheme as extendTheme } from '@mui/material';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

const theme = extendTheme({
  typography: {
    fontFamily: inter.style.fontFamily,
  },
  colorSchemes: {
    light: {
      palette: {
        primary: {
          main: '#0098EA',
        },
      },
    },
    dark: {
      // palette for dark mode
      palette: {},
    },
  },
});

export default theme;
