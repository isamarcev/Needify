'use client';
import { experimental_extendTheme as extendTheme } from '@mui/material';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

const theme = extendTheme({
  typography: {
    fontFamily: inter.style.fontFamily,
    h1: {
      fontSize: 28,
      fontWeight: 700,
      color: '#FFFFFF',
    },
    h2: {
      fontSize: 24,
      fontWeight: 700,
      color: '#FFFFFF',
    },
    h3: {
      fontSize: 16,
      fontWeight: 700,
      color: 'rgba(255,255,255,0.7)',
    },
    body1: {
      color: '#FFFFFF',
    },
    body2: {
      color: 'white',
    },
  },
  colorSchemes: {
    light: {
      palette: {
        primary: {
          main: '#0098EA',
        },
        secondary: {
          main: '#FFFFFF',
          dark: 'rgba(255,255,255,0.1)',
        },
        text: {
          primary: '#FFFFFF',
        },
        background: {
          paper: '#3b3d3e',
          default: '#3b3d3e',
        },
      },
      //@ts-expect-error
      shape: {
        borderRadius: 10,
      },
    },
    dark: {
      // palette for dark mode
      palette: {},
    },
  },
});

export default theme;
