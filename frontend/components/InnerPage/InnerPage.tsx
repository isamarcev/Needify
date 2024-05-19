import { FC } from 'react';
import { IInnerPage } from '@/components/InnerPage/types';
import styles from './InnerPage.module.css';
import { Typography } from '@mui/material';

export const InnerPage: FC<IInnerPage> = ({ title, children }) => {
  return (
    <main className={styles.main}>
      <Typography variant="h1" align="center">
        {title}
      </Typography>
      {children}
    </main>
  );
};
