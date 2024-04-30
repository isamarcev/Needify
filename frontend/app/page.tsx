'use client';
import styles from './page.module.css';
import { useTelegram } from '@/helpers/TelegramContext/TelegramContext';
import { Box, Button, CircularProgress, Typography } from '@mui/material';
import { Selector } from '@/components/Selector';
import { TaskCard } from '@/widgets/TaskCard';
import { ITaskCard } from '@/widgets/TaskCard/types';

export default function Home() {
  const { isLoading } = useTelegram();

  const categoryOptions = [
    'Psychology',
    'Plumbing',
    'Design',
    'Marketing',
    'Ads',
    'Sales',
    'Healthcare',
  ];

  const cardsData: ITaskCard[] = [
    {
      title: 'Set the google ads',
      cardData: {
        Deadline: '17.05.2024',
        Price: '250 {TIME}',
      },
    },
    {
      title: 'Set the yandex ads',
      cardData: {
        Deadline: '17.05.2024',
        Price: '250 {TIME}',
      },
    },
    {
      title: 'Develop the site',
      cardData: {
        Deadline: '17.05.2024',
        Price: '250 {TIME}',
      },
    },
    {
      title: 'Develop the site',
      cardData: {
        Deadline: '17.05.2024',
        Price: '250 {TIME}',
      },
    },
    {
      title: 'Develop the site',
      cardData: {
        Deadline: '17.05.2024',
        Price: '250 {TIME}',
      },
    },
    {
      title: 'Develop the site',
      cardData: {
        Deadline: '17.05.2024',
        Price: '250 {TIME}',
      },
    },
    {
      title: 'Develop the site',
      cardData: {
        Deadline: '17.05.2024',
        Price: '250 {TIME}',
      },
    },
    {
      title: 'Develop the site',
      cardData: {
        Deadline: '17.05.2024',
        Price: '250 {TIME}',
      },
    },
    {
      title: 'Develop the site',
      cardData: {
        Deadline: '17.05.2024',
        Price: '250 {TIME}',
      },
    },
  ];

  return isLoading ? (
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
        <Button className={styles.menuItem} variant="contained">
          My order
        </Button>
      </Box>
      <Box className={styles.category}>
        <Selector
          label="Category"
          options={categoryOptions}
          onChange={() => {}}
        />
      </Box>
      <Box className={styles.cards}>
        {cardsData.map((data) => (
          <TaskCard key={data.title} {...data} />
        ))}
      </Box>
      <Button className={styles.createOrder} variant="contained">
        Create order
      </Button>
    </main>
  );
}
