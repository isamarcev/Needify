'use client';
import { useWatch } from 'react-hook-form-mui';
import { Alert, Button, Stack } from '@mui/material';
import { useTonAddress, useTonConnectUI } from '@tonconnect/ui-react';
import { createTask, getDeployMessage } from '@/services/api';
import { useTelegram } from '@/providers/TelegramContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { is } from 'date-fns/locale';

export const SubComponent = () => {
  const fields = useWatch();
  const [tonConnectUI] = useTonConnectUI();
  const { telegramApp, isLoading } = useTelegram();
  const router = useRouter()
  const wallet = useTonAddress();

  useEffect(() => {
    let MainButtonOnClick = () => {};
    if (wallet) {
      telegramApp?.WebApp.MainButton.setParams({
        text: 'Create Task',
        color: fields.title && fields.description && fields.category && fields.price && fields.currency && fields.deadline ? telegramApp?.WebApp.themeParams.button_color : telegramApp?.WebApp.themeParams.hint_color,
        is_visible: true,
        is_active: fields.title && fields.description && fields.category && fields.price && fields.currency && fields.deadline,
      })
      MainButtonOnClick =async () => {
        if (!telegramApp?.WebApp.initDataUnsafe.user?.id) {
          return;
        }
        telegramApp.WebApp.MainButton.showProgress();
        const created_task = await createTask({
          title: fields.title,
          description: fields.description,
          category: fields.category,
          price: fields.price,
          currency: fields.currency,
          poster_id: telegramApp.WebApp.initDataUnsafe.user.id,
          deadline: fields.deadline,
        });
        telegramApp.WebApp.MainButton.hideProgress();
        if (created_task.status_code === 400) {
          telegramApp.WebApp.showAlert(created_task.error_message);
        }
        else {
          const deploy_message = await getDeployMessage({
            task_id: created_task.task_id,
            action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
          });

          const result = tonConnectUI.sendTransaction(deploy_message);
          router.replace('/task-detail/' + created_task.task_id)
          console.log(result);
        }
      }
      telegramApp?.WebApp.MainButton.onClick(MainButtonOnClick);
    }
    else {
      telegramApp?.WebApp.MainButton.enable();
      telegramApp?.WebApp.MainButton.setParams({
        text: 'Connect Wallet',
        color: telegramApp?.WebApp.themeParams.button_color,
        is_visible: true,
      })
      MainButtonOnClick = async () => {
        tonConnectUI.openModal();
      }
      telegramApp?.WebApp.MainButton.onClick(MainButtonOnClick);
    }
    
    return () => {
      telegramApp?.WebApp.MainButton.offClick(MainButtonOnClick);
      telegramApp?.WebApp.MainButton.hide();
    }
  }, [telegramApp, wallet, fields]);


  return (
    <>
      <Stack spacing={3} marginTop={2}>
        <Alert variant="outlined" severity="info">
          You have to fill out the required fields before the Button activates.
        </Alert>
      </Stack>
    </>
  );
};
