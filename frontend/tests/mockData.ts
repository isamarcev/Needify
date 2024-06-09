import { ITaskFullCard, ITaskShortCard } from '@/widgets/TaskCard/types';
import {
  ECategory,
  ETaskStatus,
  ITaskDetail,
} from '@/app/task-detail/[id]/types';

export const cardsShortData: ITaskShortCard[] = [
  {
    id: 1,
    title: 'Set the google ads',
    deadline: '17.05.2024',
    price: '250 {TIME}',
  },
  {
    id: 2,
    title: 'Set the yandex ads',
    deadline: '17.05.2024',
    price: '250 {TIME}',
  },
  {
    id: 3,
    title: 'Develop the site',
    deadline: '17.05.2024',
    price: '250 {TIME}',
  },
  {
    id: 4,
    title: 'Develop the site',
    deadline: '17.05.2024',
    price: '250 {TIME}',
  },
  {
    id: 5,
    title: 'Develop the site',
    deadline: '17.05.2024',
    price: '250 {TIME}',
  },
  {
    id: 6,
    title: 'Develop the site',
    deadline: '17.05.2024',
    price: '250 {TIME}',
  },
  {
    id: 7,
    title: 'Develop the site',
    deadline: '17.05.2024',
    price: '250 {TIME}',
  },
  {
    id: 8,
    title: 'Develop the site',
    deadline: '17.05.2024',
    price: '250 {TIME}',
  },
  {
    id: 9,
    title: 'Develop the site',
    deadline: '17.05.2024',
    price: '250 {TIME}',
  },
];

export const cardsFullData: ITaskFullCard[] = cardsShortData.map((card, i) => ({
  status:
    i === 0
      ? ETaskStatus.Created
      : i === 1
        ? ETaskStatus.Waiting
        : i === 2
          ? ETaskStatus.InProgress
          : ETaskStatus.ConfirmedByDoer,
  doer: `@user_${i}`,
  category: i % 2 ? ECategory.Marketing : ECategory.Design,
  ['task #']: card.id,
  ...card,
}));

export const taskDetailData: ITaskDetail = {
  id: 1,
  title: 'Task Title',
  description:
    "I'm the best of the best man of the best TON chain bla bla bla. I'm the best of the best man of the best TON chain bla bla bla. I'm the best of the best man of the best TON chain bla bla bla.",
  price: '250 { TIME }',
  status: ETaskStatus.Created,
  deadline: '17.05.2024',
  doer: '@username',
  category: ECategory.Marketing,
  images: [
    '/images/temp/photo-1.jpg',
    '/images/temp/photo-2.jpg',
    '/images/temp/photo-3.jpg',
  ],
};
