import { ITaskDetail } from '@/app/task-detail/[id]/types';

export type ITaskShortCard = Pick<
  ITaskDetail,
  'task_id' | 'title' | 'deadline' | 'price'
>;

export type ITaskFullCard = Omit<ITaskDetail, 'images' | 'description'> & {
  ['task #']: ITaskDetail['task_id'];
};
