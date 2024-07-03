'use client';

import { Box, Typography } from '@mui/material';
import styles from './page.module.css';
import { TaskCard } from '@/widgets/TaskCard';
// import { cardsFullData } from '@/tests/mockData';
import { InnerPage } from '@/components/InnerPage';
import { getUserTasks } from '@/services/api';
import { useEffect, useState } from 'react';
import { IUserTasks } from './types';
import { tasksRawToShortCards } from '@/helpers';
import { useTelegram } from '@/providers/TelegramContext';
import { ITaskShortCard } from '@/widgets/TaskCard/types';

export default function Page() {
  // console.log(cardsFullData)
  const { telegramApp, isLoading } = useTelegram();
  const [cardsFullData, setcardsFullData] = useState<IUserTasks>(
    {} as IUserTasks,
  );
  const [loading, setLoading] = useState(true);
  // const tasks = await getTasks();

  useEffect(() => {
    if (loading && !isLoading) {
      (async () => {
        if (!telegramApp?.WebApp?.initDataUnsafe?.user?.id) {
          return;
        }
        let cardsFullData = await getUserTasks(
          telegramApp.WebApp.initDataUnsafe.user.id,
        );
        cardsFullData.published_tasks = tasksRawToShortCards(
          cardsFullData.published_tasks,
        );
        cardsFullData.picked_up_tasks = tasksRawToShortCards(
          cardsFullData.picked_up_tasks,
        );
        cardsFullData.completed_tasks = tasksRawToShortCards(
          cardsFullData.completed_tasks,
        );
        console.log(cardsFullData);
        // cardsFullData.published_tasks = tasksRawToShortCards(cardsFullData.published_tasks)
        setcardsFullData(cardsFullData);
        setLoading(false);
      })();
    }
  });

  return loading ? (
    <Typography variant="h1">Loading...</Typography>
  ) : (
    <InnerPage title="My tasks">
      <Typography className={styles.subtitle} variant="h2">
        Published tasks
      </Typography>
      <Box className={styles.cards}>
        {cardsFullData.published_tasks.map((data) => (
          <TaskCard key={data.task_id} {...data} />
        ))}
      </Box>
      <Typography className={styles.subtitle} variant="h2">
        Picked up tasks
      </Typography>
      <Box className={styles.cards}>
        {cardsFullData.picked_up_tasks.map((data) => (
          <TaskCard key={data.task_id} {...data} />
        ))}
      </Box>
    </InnerPage>
  );
}
