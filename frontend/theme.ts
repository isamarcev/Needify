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
    },
    h2: {
      fontSize: 24,
      fontWeight: 700,
    },
    h3: {
      fontSize: 16,
      fontWeight: 700,
    },
    body2: {
      color: '#1E233780',
    },
  },
  colorSchemes: {
    light: {
      palette: {
        primary: {
          main: '#0098EA',
        },
        secondary: {
          main: '#F7F9FB',
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
