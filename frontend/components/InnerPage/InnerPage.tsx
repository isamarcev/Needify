import { FC } from 'react';
import { IInnerPage } from '@/components/InnerPage/types';
import styles from './InnerPage.module.css';
import { Typography } from '@mui/material';
import Image from 'next/image';

export const InnerPage: FC<IInnerPage> = ({ title, children }) => {
  return (
    <main className={styles.main}>
      <div className={styles.title}>
        <Image
          src="./images/needify-square.svg"
          alt="logo"
          width="48"
          height="48"
        />
        <Typography variant="h1" align="center" className={styles.text}>
          {title}
        </Typography>
      </div>
      {children}
    </main>
  );
};
