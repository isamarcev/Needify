'use client';

import styles from './page.module.css';
// import '../../trackers';
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
import linkIcon from '@/public/images/link-icon.svg';
import {
  getChooseDoerMessage,
  getCompleteMessage,
  getConfirmMessage,
  getDeployMessage,
  getGetJobMessage,
  getRevokeMessage,
  getTask,
} from '@/services/api';
import { EBottomButtonType, ITaskDetail } from './types';
import { ETaskStatus } from '@/services/types';
import { useTonConnectUI, useTonAddress } from '@tonconnect/ui-react';
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
  const { telegramApp, isLoading } = useTelegram();
  const [taskDetailData, setTaskDetailData] = useState<ITaskDetail>(
    {} as ITaskDetail,
  );
  const wallet  = useTonAddress();

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
      else if (type == EBottomButtonType.DEPLOY) {
        message = await getDeployMessage({
          task_id: taskDetailData.task_id,
          action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
        });
      }
    console.log(message);
    await tonConnectUI.sendTransaction(message);
  }

  telegramApp?.WebApp.MainButton.show();

  useEffect(() => {
    let MainButtonOnClick = async () => {
      tonConnectUI.openModal();
    }
    let MainButtonParams = {
      text: 'Connect Wallet',
      color: telegramApp?.WebApp.themeParams.button_color,
    }
    if (wallet) {
      if (telegramApp?.WebApp?.initDataUnsafe?.user?.id) {
        if (
          taskDetailData.poster_id ==
            telegramApp?.WebApp?.initDataUnsafe?.user?.id &&
          taskDetailData.status == ETaskStatus.PUBLISHED
        ) {
          MainButtonParams = {
            text: 'Revoke',
            color: telegramApp.WebApp.themeParams.destructive_text_color,
          }
          MainButtonOnClick = async () => {
            await getMessage(EBottomButtonType.REVOKE);
          }
          
        } else if (
          taskDetailData.doer_id == telegramApp?.WebApp?.initDataUnsafe?.user?.id &&
          taskDetailData.status == ETaskStatus.IN_PROGRESS
        ) {
          MainButtonParams = {
            text: 'Complete',
            color: telegramApp.WebApp.themeParams.button_color,
          }
          MainButtonOnClick = async () => {
            await getMessage(EBottomButtonType.COMPLETE);
          }
        } else if (
          taskDetailData.poster_id ==
            telegramApp?.WebApp?.initDataUnsafe?.user?.id &&
          taskDetailData.status == ETaskStatus.COMPLETED
        ) {
          MainButtonParams = {
            text: 'Confirm',
            color: telegramApp.WebApp.themeParams.button_color,
          }
          MainButtonOnClick = async () => {
            await getMessage(EBottomButtonType.CONFIRM);
          }
        } else if (
          taskDetailData.poster_id !=
            telegramApp?.WebApp?.initDataUnsafe?.user?.id &&
          taskDetailData.status == ETaskStatus.PUBLISHED
        ) {
          MainButtonParams = {
            text: 'Get Job',
            color: telegramApp.WebApp.themeParams.button_color,
          }
          MainButtonOnClick = async () => {
            await getMessage(EBottomButtonType.GET_JOB);
          }
        }
        else if (
          taskDetailData.poster_id == telegramApp?.WebApp?.initDataUnsafe?.user?.id &&
          (taskDetailData.status == ETaskStatus.PRE_CREATED || taskDetailData.status == ETaskStatus.PRE_DEPLOYING)
        ) {
          MainButtonParams = {
            text: 'Deploy',
            color: telegramApp.WebApp.themeParams.button_color,
          }
          MainButtonOnClick = async () => {
            await getMessage(EBottomButtonType.DEPLOY);
          }
        }
    }
  }
  console.log(MainButtonParams);
  console.log(MainButtonOnClick);
  telegramApp?.WebApp.MainButton.onClick(MainButtonOnClick);
  telegramApp?.WebApp.MainButton.setParams(MainButtonParams);
  telegramApp?.WebApp.MainButton.show();
  return () => {
    telegramApp?.WebApp.MainButton.offClick(MainButtonOnClick);
    telegramApp?.WebApp.MainButton.hide();
  }
}, [wallet, telegramApp, taskDetailData]);

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
            <Image
              src={linkIcon}
              alt="linkIcon"
              width={16}
              height={16}
              className={styles.linkIcon}
            />
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
    </main>
  );
}
