export interface IStore {
  user: IUser;
  setUser: (user: IUser) => void;
}

export interface IUser {
  telegram_id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  image?: string;
}
