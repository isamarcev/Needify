'use client';
import { Box, Button, Typography } from '@mui/material';
import styles from './page.module.css';
import { TaskCard } from '@/widgets/TaskCard';
import { cardsFullData } from '@/tests/mockData';
import { useRouter } from 'next/navigation';

export default function Page() {
  const router = useRouter();

  const handleBack = () => {
    router.back();
  };

  return (
    <main className={styles.main}>
      <Typography variant="h1" align="center">
        My tasks
      </Typography>
      <Typography className={styles.subtitle} variant="h2">
        Published tasks
      </Typography>
      <Box className={styles.cards}>
        {cardsFullData
          .filter((_, i) => i < 4)
          .map((data) => (
            <TaskCard key={data.id} {...data} />
          ))}
      </Box>
      <Typography className={styles.subtitle} variant="h2">
        Picked up tasks
      </Typography>
      <Box className={styles.cards}>
        {cardsFullData
          .filter((_, i) => i >= 4)
          .map((data) => (
            <TaskCard key={data.id} {...data} />
          ))}
      </Box>
      <Button
        className={styles.backBtn}
        variant="contained"
        onClick={handleBack}
      >
        Back
      </Button>
    </main>
  );
}
