'use client';
import { InnerPage } from '@/components/InnerPage';
import { ICreateTaskValues } from '@/app/create-task/types';
import styles from './page.module.css';
import {
  FormContainer,
  SelectElement,
  SubmitHandler,
  TextareaAutosizeElement,
  TextFieldElement,
} from 'react-hook-form-mui';
import { categoriesRawToOptions, currenciesRawToOptions } from '@/helpers';
import { DatePickerElement } from 'react-hook-form-mui/date-pickers';
import { SubComponent } from './components/SubmitForm';
import { useCallback, useEffect, useState } from 'react';
import { IOption } from '@/components/Selector/types';
import { createTask, getCategories, getCurrencies } from '@/services/api';
import { ICreateTaskData } from '@/services/types';

const defaultValues: ICreateTaskValues = {
  title: '',
};

export default function Page() {
  const [categoriesOptions, setCategoriesOptions] = useState<IOption[]>([]);
  const [currenciesOptions, setCurrenciesOptions] = useState<IOption[]>([]);

  useEffect(() => {
    (async () => {
      const categoriesList = await getCategories();
      setCategoriesOptions(categoriesRawToOptions(categoriesList));

      const currenciesList = await getCurrencies();
      setCurrenciesOptions(currenciesRawToOptions(currenciesList));
    })();
  }, []);

  const handleSubmit: SubmitHandler<ICreateTaskData> = useCallback(
    async (data) => {
      // TODO: add poster_id
      await createTask({ ...data, poster_id: 847057842 });
    },
    [],
  );

  return (
    <InnerPage title="Create task">
      <FormContainer defaultValues={defaultValues} onSuccess={handleSubmit}>
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
            name="images"
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
            options={categoriesOptions}
            required
          />
          <TextFieldElement name="price" label="Price" type="number" required />
          <SelectElement
            label="Currency"
            name="currency"
            options={currenciesOptions}
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
