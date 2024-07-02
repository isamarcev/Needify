'use client';
import { useState, useEffect } from 'react';
import styles from './page.module.css';
import { TonConnectButton } from '@tonconnect/ui-react';
import { useTonWallet } from '@tonconnect/ui-react';
import { InnerPage } from '@/components/InnerPage';
import {
  FormContainer,
  // SelectElement,
  // TextareaAutosizeElement,
  TextFieldElement,
} from 'react-hook-form-mui';
import {
  Button,
  // FormControl,
  // FormControlLabel,
  // InputLabel,
  // Switch,
  // Select,
  // MenuItem,
  // OutlinedInput,
  // Box,
  // Chip,
  Avatar,
} from '@mui/material';
import { addUserWallet, editUser, getUser } from '@/services/api';
import { useTelegram } from '@/providers/TelegramContext';

export default function Page() {
  const webApp = useTelegram();
  const telegramId = webApp?.initDataUnsafe?.user.id;
  const id = telegramId;
  const wallet = useTonWallet();
  const address = wallet?.account?.address;
  const [defaultValues, setDefaultValues] = useState({});

  const [isLoadingUser, setLoadingUser] = useState(true);
  const [avatar, setAvatar] = useState('');
  // const [categories, setCategories] = useState([]);
  // const [isLoadingCategories, setLoadingCategories] = useState(true);

  useEffect(() => {
    getUser(id).then((res) => {
      if (res?.web3_wallet?.address && address) {
        addUserWallet(id, {
          address,
        });
      }
      setDefaultValues((prevState) => ({
        ...prevState,
        first_name: res.first_name,
        last_name: res.last_name,
      }));
      setLoadingUser(false);
      setAvatar(res.image);
    });
    // getCategories().then((res) => {
    //   console.log(res);
    //   setCategories(res);
    //   setLoadingCategories(false);
    // });
  }, []);

  function submitForm(data) {
    const body = {
      ...data,
      image: avatar,
    };
    editUser(id, body);
  }

  function changeAvatar(event) {
    const file = event.target.files[0];

    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatar(reader.result);
      };
      reader.readAsDataURL(file);
    }
  }

  if (isLoadingUser) return <></>;

  return (
    <InnerPage title="Profile">
      <FormContainer defaultValues={defaultValues} onSuccess={submitForm}>
        <div className={styles.top}>
          <TextFieldElement
            className={styles.first_name}
            name="first_name"
            placeholder="Name"
            required
            fullWidth
          />
          <TonConnectButton />
        </div>
        <TextFieldElement
          className={styles.last_name}
          name="last_name"
          placeholder="Last name"
          fullWidth
        />
        <div className={styles.avatar}>
          <Avatar
            className={styles.avatar_image}
            sx={{
              width: 108,
              height: 108,
              bgcolor: '#0098EA',
            }}
            src={avatar}
          ></Avatar>
          <TextFieldElement
            fullWidth
            label="Photo"
            name="image"
            type="file"
            InputLabelProps={{
              shrink: true,
            }}
            inputProps={{
              accept: 'image/*',
            }}
            onChange={changeAvatar}
          />
        </div>

        {/*<div className={styles.expert}>*/}
        {/*  <FormControlLabel control={<Switch />} label="Expert profile" />*/}
        {/*</div>*/}
        {/*<TextareaAutosizeElement*/}
        {/*  fullWidth*/}
        {/*  className={styles.about}*/}
        {/*  name="about"*/}
        {/*  label="About me"*/}
        {/*  required*/}
        {/*  rows={5}*/}
        {/*/>*/}
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
        <Button className={styles.button} variant="contained" type="submit">
          Save
        </Button>
      </FormContainer>
    </InnerPage>
  );
}
