'use client';

import styles from './page.module.css';
import {
  Button,
  ImageList,
  ImageListItem,
  List,
  ListItemText,
  Paper,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import {
  getChooseDoerMessage,
  getCompleteMessage,
  getConfirmMessage,
  getGetJobMessage,
  getRevokeMessage,
  getTask,
} from '@/services/api';
import { EBottomButtonType, ITaskDetail } from './types';
import { ETaskStatus } from '@/services/types';
import { useTonConnectUI } from '@tonconnect/ui-react';
import { useTelegram } from '@/providers/TelegramContext';
import Link from 'next/link';
import Image from 'next/image';

interface IProps {
  params: {
    id: number;
  };
}

export default function Page({ params: { id } }: IProps) {
  const [tonConnectUI] = useTonConnectUI();
  const [taskDetailData, setTaskDetailData] = useState<ITaskDetail>(
    {} as ITaskDetail,
  );
  const { telegramApp } = useTelegram();

  const {
    title,
    currency,
    price,
    status,
    deadline,
    description,
    job_offer,
    poster_id,
    task_id,
  } = taskDetailData;

  useEffect(() => {
    (async () => {
      const taskDetailData = await getTask(id);
      setTaskDetailData(taskDetailData);
    })();
  }, [id]);

  async function getMessage(type: EBottomButtonType) {
    let message;
    if (telegramApp?.WebApp.initDataUnsafe.user?.id)
      if (type === EBottomButtonType.REVOKE) {
        message = await getRevokeMessage({
          task_id: taskDetailData.task_id,
          action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
        });
      } else if (type === EBottomButtonType.COMPLETE) {
        message = await getCompleteMessage({
          task_id: taskDetailData.task_id,
          action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
        });
      } else if (type === EBottomButtonType.GET_JOB) {
        message = await getGetJobMessage({
          task_id: taskDetailData.task_id,
          action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
        });
      } else if (type === EBottomButtonType.CONFIRM) {
        message = await getConfirmMessage({
          task_id: taskDetailData.task_id,
          action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
          mark: 5,
          review: 'Good Job',
        });
      }

    await tonConnectUI.sendTransaction(message);
  }

  let bottom_button = null;
  if (telegramApp?.WebApp.initDataUnsafe.user?.id) {
    console.log('tut');
    if (
      taskDetailData.poster_id ===
        telegramApp?.WebApp.initDataUnsafe.user?.id &&
      taskDetailData.status === ETaskStatus.PUBLISHED
    ) {
      bottom_button = (
        <Button
          variant="contained"
          color="error"
          onClick={async () => {
            await getMessage(EBottomButtonType.REVOKE);
          }}
        >
          Revoke
        </Button>
      );
    } else if (
      taskDetailData.doer_id === telegramApp?.WebApp.initDataUnsafe.user?.id &&
      taskDetailData.status === ETaskStatus.IN_PROGRESS
    ) {
      bottom_button = (
        <Button
          variant="contained"
          color="primary"
          onClick={async () => {
            await getMessage(EBottomButtonType.COMPLETE);
          }}
        >
          Complete
        </Button>
      );
    } else if (
      taskDetailData.poster_id ===
        telegramApp?.WebApp.initDataUnsafe.user?.id &&
      taskDetailData.status === ETaskStatus.COMPLETED
    ) {
      bottom_button = (
        <Button
          variant="contained"
          color="primary"
          onClick={async () => {
            await getMessage(EBottomButtonType.CONFIRM);
          }}
        >
          Confirm
        </Button>
      );
    } else if (
      taskDetailData.poster_id !==
        telegramApp?.WebApp.initDataUnsafe.user?.id &&
      taskDetailData.status === ETaskStatus.PUBLISHED
    ) {
      bottom_button = (
        <Button
          variant="contained"
          color="primary"
          onClick={async () => {
            await getMessage(EBottomButtonType.GET_JOB);
          }}
        >
          Get Job
        </Button>
      );
      if (taskDetailData.job_offer) {
        if (taskDetailData.job_offer.vacancies) {
          let doers_id = taskDetailData.job_offer.vacancies.map(
            (item) => item.telegram_id,
          );
          if (telegramApp?.WebApp.initDataUnsafe.user?.id)
            if (
              doers_id.includes(telegramApp?.WebApp.initDataUnsafe.user?.id)
            ) {
              bottom_button = null;
            }
        }
      }
    }
  }

  let images = taskDetailData.images ? (
    <ImageList>
      {taskDetailData.images.map((item) => (
        <ImageListItem key={item}>
          <Image src={item} width={200} height={200} loading="lazy" alt="" />
        </ImageListItem>
      ))}
    </ImageList>
  ) : null;

  return !title ? null : (
    <main className={styles.taskDetail}>
      <Typography className={styles.title} variant="h1">
        {title}
      </Typography>
      <Paper className={styles.traitsWrapper} elevation={3}>
        <Typography variant="h3">Task #</Typography>
        <Typography variant="body1">{id}</Typography>
        <Typography variant="h3">Price</Typography>
        <Typography variant="body1">{`${price} ${currency}`}</Typography>
        <Typography variant="h3">Status</Typography>
        <Typography variant="body1">{status}</Typography>
        <Typography variant="h3">TON Explorer</Typography>
        <Typography variant="body1">
          <Link href={job_offer?.job_offer_url ?? ''} target="_blank">
            {job_offer?.job_offer_address
              ? `${job_offer.job_offer_address.slice(0, 6)}...${job_offer.job_offer_address.slice(-6)}`
              : '-'}
          </Link>
        </Typography>
        <Typography variant="h3">Deadline</Typography>
        <Typography variant="body1">
          {new Date(deadline).toLocaleDateString()}
        </Typography>
      </Paper>
      <Typography variant="body1">{description}</Typography>
      <Typography variant="h2" align="center">
        Offers
      </Typography>
      <List className={styles.offersWrapper}>
        {job_offer?.vacancies?.length ? (
          job_offer.vacancies.map(({ doer }) => (
            <Paper key={doer} className={styles.offerItem}>
              <ListItemText
                primary={`${doer.slice(0, 6)}...${doer.slice(-6)}`}
              />
              <Button
                variant="contained"
                color="primary"
                size="small"
                className={styles.offerButton}
                disabled={
                  poster_id !== telegramApp?.WebApp.initDataUnsafe.user?.id
                }
                onClick={async () => {
                  if (telegramApp?.WebApp.initDataUnsafe.user?.id) {
                    const message = await getChooseDoerMessage({
                      task_id: task_id,
                      doer,
                      action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
                    });
                    await tonConnectUI.sendTransaction(message);
                  }
                }}
              >
                Choose
              </Button>
            </Paper>
          ))
        ) : (
          <Typography variant="body1">No offers yet</Typography>
        )}
      </List>
      {images}
      {bottom_button}
    </main>
  );
}
