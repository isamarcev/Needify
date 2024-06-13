'use client';
import axios from 'axios';
import { TonConnectButton } from '@tonconnect/ui-react';
import styles from './page.module.css';
import { IProfileValues } from './types';
import { InnerPage } from '@/components/InnerPage';
import {
  FormContainer,
  SelectElement,
  TextareaAutosizeElement,
  TextFieldElement,
} from 'react-hook-form-mui';
import {
  Button,
  FormControl,
  FormControlLabel,
  InputLabel,
  Switch,
  Select,
  MenuItem,
  OutlinedInput,
  Box,
  Chip,
} from '@mui/material';
import { getOptionsFromEnum } from '@/helpers';
import { ECurrency } from '@/app/task-detail/[id]/types';
//
// const connector = new TonConnect();
//
// console.log(connector);
// connector.restoreConnection();

const defaultValues: IProfileValues = {
  name: '',
};

axios.get('http://206.189.57.147/');

export default function Page() {
  return (
    <InnerPage title="Profile">
      <FormContainer
        defaultValues={defaultValues}
        onSuccess={(data) => {
          console.log(data);
        }}
      >
        <div className={styles.top}>
          <TextFieldElement
            className={styles.name}
            name="name"
            label="Name"
            required
            fullWidth
          />
          <TonConnectButton />
        </div>
        <div className={styles.avatar}></div>
        <TextFieldElement
          fullWidth
          name="photo"
          label="Photo"
          type="file"
          InputLabelProps={{
            shrink: true,
          }}
          inputProps={{
            accept: 'image/*',
          }}
        />
        <div className={styles.expert}>
          <FormControlLabel
            control={<Switch defaultChecked />}
            name="isExpert"
            label="Expert profile"
          />
        </div>
        <TextareaAutosizeElement
          fullWidth
          className={styles.wholeLine}
          name="about"
          label="About me"
          required
          rows={5}
        />
        {/*<FormControl sx={{ m: 1, width: 300 }}>*/}
        {/*  <InputLabel id="demo-multiple-chip-label">Chip</InputLabel>*/}
        {/*  <Select*/}
        {/*    labelId="demo-multiple-chip-label"*/}
        {/*    id="demo-multiple-chip"*/}
        {/*    multiple*/}
        {/*    value={personName}*/}
        {/*    onChange={handleChange}*/}
        {/*    input={<OutlinedInput id="select-multiple-chip" label="Chip" />}*/}
        {/*    renderValue={(selected) => (*/}
        {/*      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>*/}
        {/*        {selected.map((value) => (*/}
        {/*          <Chip key={value} label={value} />*/}
        {/*        ))}*/}
        {/*      </Box>*/}
        {/*    )}*/}
        {/*    MenuProps={MenuProps}*/}
        {/*  >*/}
        {/*    {names.map((name) => (*/}
        {/*      <MenuItem*/}
        {/*        key={name}*/}
        {/*        value={name}*/}
        {/*        style={getStyles(name, personName, theme)}*/}
        {/*      >*/}
        {/*        {name}*/}
        {/*      </MenuItem>*/}
        {/*    ))}*/}
        {/*  </Select>*/}
        {/*</FormControl>*/}
        <Button variant="contained" type="submit">
          Save
        </Button>
      </FormContainer>
    </InnerPage>
  );
}
