import { ITaskDetail } from '@/app/task-detail/[id]/types';

export type ITaskShortCard = Pick<
  ITaskDetail,
  'id' | 'title' | 'deadline' | 'price'
>;

export type ITaskFullCard = Omit<ITaskDetail, 'images' | 'description'> & {
  ['task #']: ITaskDetail['id'];
};
