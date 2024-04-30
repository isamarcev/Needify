import { FC } from 'react';
import { ITaskCard } from '@/widgets/TaskCard/types';
import { Paper, Typography } from '@mui/material';
import styles from './taskCard.module.css';
import Link from 'next/link';

export const TaskCard: FC<ITaskCard> = ({ title, cardData }) => {
  console.log(cardData);
  return (
    <Link href={`/${title}`}>
      <Paper className={styles.taskCardWrapper} elevation={3}>
        <Typography variant="h3">{title}</Typography>
        <div className={styles.cardDataWrapper}>
          {Object.entries(cardData).map(([key, value]) => (
            <div key={`${key}-${value}`}>
              <Typography variant="body2">{key}</Typography>
              <Typography variant="body1">{value}</Typography>
            </div>
          ))}
        </div>
      </Paper>
    </Link>
  );
};
