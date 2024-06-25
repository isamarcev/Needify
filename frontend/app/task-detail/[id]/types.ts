export interface ITaskDetail {
  id: number;
  title: string;
  description: string;
  price: number;
  status: ETaskStatus;
  deadline: string;
  doer: string;
  category: ECategory;
  images: string[];
}

export enum ETaskStatus {
  Created = 'Created',
  Waiting = 'Waiting for the Doer',
  InProgress = 'In progress',
  ConfirmedByDoer = 'Confirmed by Doer',
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
  TON = 'TON',
  USDT = 'USDT',
  NOT = 'NOT',
  ETH = 'ETH',
}
