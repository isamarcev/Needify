'use client';
import styles from './page.module.css';
import { useTelegram } from '@/providers/TelegramContext';
import { Box, Button, CircularProgress } from '@mui/material';
import { Selector } from '@/components/Selector';
import { TaskCard } from '@/widgets/TaskCard';
import Link from 'next/link';
import { categoriesRawToOptions, tasksRawToShortCards } from '@/helpers';
import Image from 'next/image';
import { useEffect, useState } from 'react';
import { getCategories, getTasks } from '@/services/api';
import { IOption } from '@/components/Selector/types';
import { ITaskShortCard } from '@/widgets/TaskCard/types';

export default function Home() {
  const { isLoading } = useTelegram();
  const [categoriesOptions, setCategoriesOptions] = useState<IOption[]>([]);
  const [tasks, setTasks] = useState<ITaskShortCard[]>([]);

  useEffect(() => {
    (async () => {
      const categoriesList = await getCategories();
      setCategoriesOptions(categoriesRawToOptions(categoriesList));

      const tasksList = await getTasks();
      setTasks(tasksRawToShortCards(tasksList));
    })();
  }, []);

  return isLoading ? (
    <Box className={styles.loader}>
      <CircularProgress />
    </Box>
  ) : (
    <main className={styles.main}>
      <Image
        className={styles.logo}
        src="./images/needify-text.svg"
        alt="logo"
        width="164"
        height="32"
      />
      <Box className={styles.menuWrapper}>
        <Link href="/profile" passHref>
          <Button className={styles.menuItem} variant="outlined">
            Profile
          </Button>
        </Link>
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
          options={categoriesOptions}
          onChange={() => {}}
        />
      </Box>
      <Box className={styles.cards}>
        {tasks.map((data) => (
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
