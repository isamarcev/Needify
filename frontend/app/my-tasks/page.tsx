'use client';
import { Box, Typography } from '@mui/material';
import styles from './page.module.css';
import { TaskCard } from '@/widgets/TaskCard';
import { cardsFullData } from '@/tests/mockData';
import { InnerPage } from '@/components/InnerPage';

export default function Page() {
  return (
    <InnerPage title="My tasks">
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
    </InnerPage>
  );
}
