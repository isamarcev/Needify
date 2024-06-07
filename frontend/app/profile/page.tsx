'use client';
// import { TonConnectButton } from '@tonconnect/ui-react';
import styles from './page.module.css';
import { IProfileValues } from './types';
import { InnerPage } from '@/components/InnerPage';
import { FormContainer, TextFieldElement } from 'react-hook-form-mui';
import TonConnect from '@tonconnect/sdk';
import { Button } from '@mui/material';

const connector = new TonConnect();

console.log(connector);
connector.restoreConnection();

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
        <Button variant="contained">Customer profile</Button>
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
