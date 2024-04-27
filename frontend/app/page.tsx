'use client';
import styles from './page.module.css';
import { useTelegram } from '@/helpers/TelegramContext/TelegramContext';
import { Box, CircularProgress } from '@mui/material';

export default function Home() {
  const { isLoading } = useTelegram();

  return isLoading ? (
    <Box className={styles.loader}>
      <CircularProgress />
    </Box>
  ) : (
    <main className={styles.main}>
      <p>Main page will be here</p>
    </main>
  );
}
