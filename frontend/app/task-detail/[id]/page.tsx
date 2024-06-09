import styles from './page.module.css';
import { ImageList, ImageListItem, Typography } from '@mui/material';
import { taskDetailData } from '@/tests/mockData';

interface IProps {
  params: {
    id: number;
  };
}

export default function Page(props: IProps) {
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
        {taskDetailData.title}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Description
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {taskDetailData.description}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Price
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {taskDetailData.price}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Status
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {taskDetailData.status}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Deadline
      </Typography>
      <Typography className={styles.taskDescription} variant="body1">
        {taskDetailData.deadline}
      </Typography>
      <Typography className={styles.taskTitle} variant="h3">
        Images
      </Typography>
      <ImageList className={styles.taskDescription} cols={2}>
        {taskDetailData.images.map((item) => (
          <ImageListItem key={item}>
            <img src={item} width={200} height={200} loading="lazy" alt="" />
          </ImageListItem>
        ))}
      </ImageList>
    </main>
  );
}
