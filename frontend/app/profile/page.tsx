'use client';
// import { TonConnectButton } from '@tonconnect/ui-react';
import styles from './page.module.css';
import { IProfileValues } from './types';
import { InnerPage } from '@/components/InnerPage';
import { FormContainer, TextFieldElement } from 'react-hook-form-mui';

const defaultValues: IProfileValues = {
  name: '',
};

export default function Page() {
  return (
    <InnerPage title="Profile">
      <FormContainer
        defaultValues={defaultValues}
        onSuccess={(data) => {
          console.log(data);
        }}
      >
        <div></div>
        <div className={styles.top}>
          <TextFieldElement
            className={styles.wholeLine}
            name="name"
            label="Name"
            required
          />

          {/*<TonConnectButton />*/}
        </div>
        <div className={styles.avatar}></div>
        <div className={styles.expert}></div>
      </FormContainer>
    </InnerPage>
  );
}
