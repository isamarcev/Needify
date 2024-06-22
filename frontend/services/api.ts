import {
  AddUserWalletParams,
  EditUserParams,
  ETaskStatus,
  ICategoryRaw,
  ITaskRaw,
} from '@/services/types';

const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;

// Users
export async function getUsers() {
  const res = await fetch(`${BASE_URL}/v1/users/list`, { mode: 'no-cors' });

  if (!res.ok) {
    throw new Error('Failed to get users');
  }

  return res.json();
}

export async function getUser(id: number) {
  const res = await fetch(`${BASE_URL}/v1/users/${id}`);

  if (!res.ok) {
    throw new Error('Failed to get users');
  }

  return res.json();
}

export async function createUser(params: EditUserParams) {
  const res = await fetch(`${BASE_URL}/v1/users`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error('Failed to create user');
  }

  return res.json();
}

export async function editUser(id: number, params: EditUserParams) {
  const res = await fetch(`${BASE_URL}/v1/users/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error('Failed to get users');
  }

  return res.json();
}

export async function addUserWallet(id: number, params: AddUserWalletParams) {
  const res = await fetch(`${BASE_URL}/v1/users/wallet/add?telegram_id=${id}`, {
    method: 'POST',
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error('Failed to add user wallet');
  }

  return res.json();
}

// Currency

// Task
export async function getTasks(params: {
  category: string;
  status?: ETaskStatus;
}): Promise<ITaskRaw[]> {
  const searchParams = new URLSearchParams(params);

  const res = await fetch(`${BASE_URL}/v1/task?${searchParams}`);

  if (!res.ok) {
    throw new Error('Failed to get tasks');
  }

  return res.json();
}

export async function getTask(id: number) {
  const res = await fetch(`${BASE_URL}/v1/task/${id}`);

  if (!res.ok) {
    throw new Error('Failed to get task');
  }

  return res.json();
}

// Job-offer

// Category
export async function getCategories(): Promise<ICategoryRaw[]> {
  const res = await fetch(`${BASE_URL}/v1/category`);

  if (!res.ok) {
    throw new Error('Failed to get categories');
  }

  return res.json();
}

// Ton-connect
