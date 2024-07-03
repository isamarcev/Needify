import { ETaskStatus } from '@/services/types';

export interface ITaskDetail {
  task_id: number;
  title: string;
  description: string;
  price: number;
  status: ETaskStatus;
  deadline: string;
  poster_id: number;
  doer_id: number | null;
  category: ECategory;
  currency: ECurrency;
  images: string[];
  job_offer: IJobOffer | null;
}

export interface IJobOffer {
    vacancies: IDoer[] | null;
}

export interface IDoer {
    doer: string;
    telegram_id: number;
}

export enum EBottomButtonType {
    REVOKE = 'REVOKE',
    COMPLETE = 'COMPLETE',
    GET_JOB = 'GET_JOB',
    CONFIRM = 'CONFIRM',
}

export enum ECategory {
  Psychology = 'Psychology',
  Plumbing = 'Plumbing',
  Design = 'Design',
  Marketing = 'Marketing',
  Ads = 'Ads',
  Sales = 'Sales',
  Healthcare = 'Healthcare',
}

export enum ECurrency {
  TUSDT = 'TUSDT',
}
