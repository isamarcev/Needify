'use client';

import styles from './page.module.css';
import {
  ImageList,
  ImageListItem,
  Typography,
  Button,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
} from '@mui/material';
// import { taskDetailData } from '@/tests/mockData';
import { useEffect, useState } from 'react';
import {
  getTask,
  getRevokeMessage,
  getCompleteMessage,
  getGetJobMessage,
  getChooseDoerMessage,
  getConfirmMessage,
} from '@/services/api';
import { ITaskDetail, EBottomButtonType } from './types';
import { ETaskStatus } from '@/services/types';
import {
  TonConnect,
  useTonAddress,
  useTonConnectUI,
} from '@tonconnect/ui-react';
import { useTelegram } from '@/providers/TelegramContext';

interface IProps {
  params: {
    id: number;
  };
}

export default function Page(props: IProps) {
  // function handleClick({ target }) {
  //   if (!document.fullscreenEnabled) {
  //     target.requestFullscreen().catch((err) => console.log(err));
  //   } else {
  //     document.exitFullscreen().catch((err) => console.log(err));
  //   }
  // }
  const [tonConnectUI, setOptions] = useTonConnectUI();
  const { telegramApp, isLoading } = useTelegram();

  async function getMessage(type: EBottomButtonType) {
    let message;
    if (telegramApp?.WebApp?.initDataUnsafe?.user?.id)
      if (type == EBottomButtonType.REVOKE) {
        message = await getRevokeMessage({
          task_id: taskDetailData.task_id,
          action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
        });
      } else if (type == EBottomButtonType.COMPLETE) {
        message = await getCompleteMessage({
          task_id: taskDetailData.task_id,
          action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
        });
      } else if (type == EBottomButtonType.GET_JOB) {
        message = await getGetJobMessage({
          task_id: taskDetailData.task_id,
          action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
        });
      } else if (type == EBottomButtonType.CONFIRM) {
        message = await getConfirmMessage({
          task_id: taskDetailData.task_id,
          action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
          mark: 5,
          review: 'Good Job',
        });
      }

    await tonConnectUI.sendTransaction(message);
  }

  const [taskDetailData, setTaskDetailData] = useState<ITaskDetail>(
    {} as ITaskDetail,
  );
  useEffect(() => {
    (async () => {
      const taskDetailData = await getTask(props.params.id);
      setTaskDetailData(taskDetailData);
    })();
  }, []);

  let bottom_button = null;
  if (!telegramApp?.WebApp?.initDataUnsafe?.user?.id) {
    if (
      taskDetailData.poster_id ==
        telegramApp?.WebApp?.initDataUnsafe?.user?.id &&
      taskDetailData.status == ETaskStatus.PUBLISHED
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
      taskDetailData.doer_id == telegramApp?.WebApp?.initDataUnsafe?.user?.id &&
      taskDetailData.status == ETaskStatus.IN_PROGRESS
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
      taskDetailData.poster_id ==
        telegramApp?.WebApp?.initDataUnsafe?.user?.id &&
      taskDetailData.status == ETaskStatus.COMPLETED
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
      taskDetailData.poster_id !=
        telegramApp?.WebApp?.initDataUnsafe?.user?.id &&
      taskDetailData.status == ETaskStatus.PUBLISHED
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
          if (telegramApp?.WebApp?.initDataUnsafe?.user?.id)
            if (
              doers_id.includes(telegramApp?.WebApp?.initDataUnsafe?.user?.id)
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
          <img src={item} width={200} height={200} loading="lazy" alt="" />
        </ImageListItem>
      ))}
    </ImageList>
  ) : null;

  return !taskDetailData.title ? null : (
    <main className={styles.taskDetail}>
      <Typography className={styles.taskNumber} variant="body1">
        Task #: {props.params.id}
      </Typography>
      <Typography className={styles.title} variant="h2">
        {taskDetailData.title}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Description
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {taskDetailData.description}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Price
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {taskDetailData.price}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Status
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {taskDetailData.status}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Deadline
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {taskDetailData.deadline}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Vacancies
      </Typography>
      <List>
        {taskDetailData.job_offer
          ? taskDetailData.job_offer.vacancies
            ? taskDetailData.job_offer.vacancies.map((item) => (
                <ListItem key={item.doer}>
                  <ListItemText primary={item.doer} />
                  <Button
                    variant="contained"
                    color="primary"
                    size="small"
                    className="choose-doer-button"
                    disabled={
                      taskDetailData.poster_id !=
                      telegramApp?.WebApp?.initDataUnsafe?.user?.id
                    }
                    onClick={async () => {
                      if (telegramApp?.WebApp?.initDataUnsafe?.user?.id) {
                        const message = await getChooseDoerMessage({
                          task_id: taskDetailData.task_id,
                          doer: item.doer,
                          action_by_user:
                            telegramApp.WebApp.initDataUnsafe.user.id,
                        });
                        await tonConnectUI.sendTransaction(message);
                      }
                    }}
                  >
                    Choose
                  </Button>
                </ListItem>
              ))
            : null
          : null}
      </List>
      {/* <ImageList className={styles.taskDescription} cols={2}  >
        {taskDetailData.images.map((item) => (
          <ImageListItem key={item}>
            <img src={item} width={200} height={200} loading="lazy" alt="" />
          </ImageListItem>
        ))}
      </ImageList> */}
      {images}
      {bottom_button}
    </main>
  );
}
