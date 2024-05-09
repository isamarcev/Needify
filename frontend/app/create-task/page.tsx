'use client';
import { InnerPage } from '@/components/InnerPage';
import { useForm } from 'react-hook-form';
import { ICreateTaskValues } from '@/app/create-task/types';
import { FormInputText } from '@/components/FormComponents/FormInputText';
import styles from './page.module.css';

const defaultValues: ICreateTaskValues = {
  title: '',
};

export default function Page() {
  const { handleSubmit, reset, control, setValue } = useForm<ICreateTaskValues>(
    { defaultValues },
  );

  const onSubmit = (data: ICreateTaskValues) => console.log(data);

  return (
    <InnerPage title="Create task">
      <div className={styles.form}>
        <FormInputText
          className={styles.title}
          name="title"
          control={control}
          label="Task title"
        />
        <FormInputText
          className={styles.title}
          name="Description"
          control={control}
          label="Description"
          multiline
          rows={4}
        />
      </div>
    </InnerPage>
  );
}
