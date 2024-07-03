export interface CreateUserParams {
  telegram_id: number;
  first_name: string;
  username?: string;
  last_name?: string;
  image?: string;
}

export interface EditUserParams {
  first_name: string;
  last_name?: string;
  image?: string;
}

export interface AddUserWalletParams {
  address: string;
}

export interface ICategoryRaw {
  title: string;
  description: string;
}

export enum ETaskStatus {
  'PRE_CREATED' = 'PRE_CREATED',
  'PRE_DEPLOYING' = 'PRE_DEPLOYING',
  'DEPLOYING' = 'DEPLOYING',
  'PUBLISHED' = 'PUBLISHED',
  'CLOSED' = 'CLOSED',
  'IN_PROGRESS' = 'IN_PROGRESS',
  'COMPLETED' = 'COMPLETED',
  'CONFIRMED' = 'CONFIRMED',
  'FINISHED' = 'FINISHED',
  'REVOKED' = 'REVOKED',
}

export interface ITaskRaw {
  task_id: number;
  title: string;
  description: string;
  images: string[];
  category: string;
  price: number;
  currency: string;
  status: ETaskStatus;
  poster_id: number;
  poster_address: string;
  doer_id: number | null;
  doer_address: string | null;
  job_offer: {
    job_offer_address: string;
    jetton_master_address: string;
    jetton_native_address: string;
    state: string;
    stateInit: string;
    owner: string;
    doer: string | null;
    vacancies: [
      {
        doer: string;
        telegram_id: number;
      },
    ];
    mark: number | null;
    review: string | null;
  };
  deadline: string;
  created_at: string;
  updated_at: string | null;
}

export interface ICreateTaskData {
  title: string;
  description: string;
  category: string;
  images: string[];
  price: number;
  currency: string;
  poster_id: number;
  deadline: string;
}

export interface ICurrency {
  address: string;
  decimals: 6;
  symbol: string;
  name: string;
  image: string;
  is_active: boolean;
  description: string;
}

export interface IUserRaw {
  _id: string;
  telegram_id: number;
  first_name?: string;
  last_name?: string;
  username?: string;
  image?: string;
  web3_wallet?: IWebWallet;
  created: string;
  updated?: string;
}

export interface IWebWallet {
  address: string;
}
