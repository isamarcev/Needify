'use client';
import { InnerPage } from '@/components/InnerPage';
import { ICreateTaskValues } from '@/app/create-task/types';
import styles from './page.module.css';
import {
  FormContainer,
  SelectElement,
  TextareaAutosizeElement,
  TextFieldElement,
} from 'react-hook-form-mui';
import { getOptionsFromEnum } from '@/helpers';
import { ECategory, ECurrency } from '@/app/task-detail/[id]/types';
import { DatePickerElement } from 'react-hook-form-mui/date-pickers';
import { SubComponent } from './components/SubmitForm';

const defaultValues: ICreateTaskValues = {
  title: '',
};

export default function Page() {
  return (
    <InnerPage title="Create task">
      <FormContainer
        defaultValues={defaultValues}
        onSuccess={(data) => {
          console.log(data);
        }}
      >
        <div className={styles.form}>
          <TextFieldElement
            className={styles.wholeLine}
            name="title"
            label="Title"
            required
          />
          <TextareaAutosizeElement
            className={styles.wholeLine}
            name="description"
            label="Description"
            rows={3}
            required
          />
          <TextFieldElement
            className={styles.wholeLine}
            name="photo"
            label="Photo"
            type="file"
            InputLabelProps={{
              shrink: true,
            }}
            inputProps={{
              multiple: true,
              accept: 'image/*',
            }}
          />
          <SelectElement
            className={styles.wholeLine}
            label="Category"
            name="category"
            options={getOptionsFromEnum(ECategory)}
            required
          />
          <TextFieldElement name="price" label="Price" type="number" required />
          <SelectElement
            label="Currency"
            name="currency"
            options={getOptionsFromEnum(ECurrency)}
            required
          />
          <DatePickerElement
            className={styles.wholeLine}
            name="deadline"
            label="Deadline"
            required
          />
        </div>
        <SubComponent />
      </FormContainer>
    </InnerPage>
  );
}
