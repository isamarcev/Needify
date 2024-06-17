export interface EditUserParams {
  first_name: string;
  last_name?: string;
  image?: string;
}

export interface AddUserWalletParams {
  telegramId: number;
  address: string;
}
