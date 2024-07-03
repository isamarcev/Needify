import { useWatch } from 'react-hook-form-mui';
import { Alert, Button, Stack } from '@mui/material';
import { useTonAddress, useTonConnectUI } from '@tonconnect/ui-react';
import { createTask, getDeployMessage } from '@/services/api';
import { useTelegram } from '@/providers/TelegramContext';

export const SubComponent = () => {
  const fields = useWatch();
  const [tonConnectUI, setOptions] = useTonConnectUI();
  const { telegramApp, isLoading } = useTelegram();

  return (
    <>
      <Stack spacing={3} marginTop={2}>
        <Button
          type="submit"
          color="primary"
          variant="contained"
          disabled={!fields.title}
          onClick={async () => {
            const created_task = await createTask({
              title: fields.title,
              description: fields.description,
              category: fields.category,
              price: fields.price,
              currency: fields.currency,
              poster_id: telegramApp.WebApp.initDataUnsafe.user.id,
              deadline: fields.deadline,
            });

            const deploy_message = await getDeployMessage({
              task_id: created_task.task_id,
              action_by_user: telegramApp.WebApp.initDataUnsafe.user.id,
            });

            const result = await tonConnectUI.sendTransaction(deploy_message);
            console.log(result);
          }}
        >
          Submit
        </Button>
        <Alert variant="outlined" severity="info">
          You have to fill out the required fields before the Button activates.
        </Alert>
      </Stack>
    </>
  );
};
