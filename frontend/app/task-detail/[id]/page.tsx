import styles from './page.module.css';
import { ImageList, ImageListItem, Typography } from '@mui/material';
import { ITaskDetail } from './types';

interface IProps {
  params: {
    id: number;
  };
}

export default function Page(props: IProps) {
  const data: ITaskDetail = {
    title: 'Task Title',
    description:
      "I'm the best of the best man of the best TON chain bla bla bla. I'm the best of the best man of the best TON chain bla bla bla. I'm the best of the best man of the best TON chain bla bla bla.",
    price: '250 { TIME }',
    status: 'Created',
    deadline: '17.05.2024',
    images: [
      '/images/temp/photo-1.jpg',
      '/images/temp/photo-2.jpg',
      '/images/temp/photo-3.jpg',
    ],
  };

  // function handleClick({ target }) {
  //   if (!document.fullscreenEnabled) {
  //     target.requestFullscreen().catch((err) => console.log(err));
  //   } else {
  //     document.exitFullscreen().catch((err) => console.log(err));
  //   }
  // }

  return (
    <main className={styles.taskDetail}>
      <Typography className={styles.logo} variant="h1" align="center">
        The Open Times
      </Typography>
      <Typography className={styles.taskNumber} variant="body1">
        Task #: {props.params.id}
      </Typography>
      <Typography className={styles.title} variant="h2">
        {data.title}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Description
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {data.description}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Price
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {data.price}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Status
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {data.status}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Deadline
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {data.deadline}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Images
      </Typography>
      <ImageList className={styles.taskDescription} cols={2}>
        {data.images.map((item) => (
          <ImageListItem key={item}>
            <img src={item} width={200} height={200} loading="lazy" alt="" />
          </ImageListItem>
        ))}
      </ImageList>
    </main>
  );
}
