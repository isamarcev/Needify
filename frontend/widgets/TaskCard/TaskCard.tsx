import { FC } from 'react';
import { ITaskShortCard } from '@/widgets/TaskCard/types';
import { Paper, Typography } from '@mui/material';
import styles from './taskCard.module.css';
import Link from 'next/link';

export const TaskCard: FC<ITaskShortCard> = ({ id, title, ...rest }) => {
  return (
    <Link href={`/task-detail/${id}`}>
      <Paper className={styles.taskCardWrapper} elevation={3}>
        <Typography variant="h3">{title}</Typography>
        <div className={styles.cardDataWrapper}>
          {Object.entries(rest).map(([key, value]) => (
            <div key={`${key}-${value}`}>
              <Typography className={styles.propertyName} variant="body2">
                {key}
              </Typography>
              <Typography variant="body1">{value}</Typography>
            </div>
          ))}
        </div>
      </Paper>
    </Link>
  );
};
