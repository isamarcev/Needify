'use client';
// import { TonConnectButton } from '@tonconnect/ui-react';
// import TonConnect from '@tonconnect/sdk';
import styles from './page.module.css';
import { IProfileValues } from './types';
import { InnerPage } from '@/components/InnerPage';
import {
  FormContainer,
  TextareaAutosizeElement,
  TextFieldElement,
} from 'react-hook-form-mui';
import {
  Button,
  FormControlLabel,
  Switch,
  Select,
  MenuItem,
} from '@mui/material';
//
// const connector = new TonConnect();
//
// console.log(connector);
// connector.restoreConnection();

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
        <div className={styles.expert}>
          <FormControlLabel
            control={<Switch defaultChecked />}
            name="isExpert"
            label="Expert profile"
          />
        </div>

        <TextareaAutosizeElement
          className={styles.wholeLine}
          name="about"
          label="About me"
          required
          rows={5}
        />

        <Select>
          <MenuItem value={1}>One</MenuItem>
        </Select>
        <TextFieldElement
          className={styles.wholeLine}
          name="name"
          label="I'm expret in"
          required
        />

        {/*<Button variant="contained">Subscribe to categories</Button>*/}
      </FormContainer>
    </InnerPage>
  );
}
