'use client';
import styles from './page.module.css';
import { useTelegram } from '@/helpers/TelegramContext/TelegramContext';
import { Box, Button, CircularProgress, Typography } from '@mui/material';
import { Selector } from '@/components/Selector';
import { TaskCard } from '@/widgets/TaskCard';
import Link from 'next/link';
import { cardsShortData } from '@/tests/mockData';
import { ECategory } from '@/app/task-detail/[id]/types';

export default function Home() {
  const { isLoading } = useTelegram();

  const categoryOptions = Object.values(ECategory);

  return !isLoading ? (
    <Box className={styles.loader}>
      <CircularProgress />
    </Box>
  ) : (
    <main className={styles.main}>
      <Typography variant="h1" align="center">
        The Open Times
      </Typography>
      <Box className={styles.menuWrapper}>
        <Button className={styles.menuItem} variant="outlined">
          Profile
        </Button>
        <Link href="/my-tasks" passHref>
          <Button
            className={styles.menuItem}
            variant="contained"
            component="span"
          >
            My tasks
          </Button>
        </Link>
      </Box>
      <Box className={styles.category}>
        <Selector
          label="Category"
          options={categoryOptions}
          onChange={() => {}}
        />
      </Box>
      <Box className={styles.cards}>
        {cardsShortData.map((data) => (
          <TaskCard key={data.id} {...data} />
        ))}
      </Box>
      <Link href="/create-task">
        <Button
          className={styles.createOrder}
          variant="contained"
          component="div"
        >
          Create task
        </Button>
      </Link>
    </main>
  );
}
