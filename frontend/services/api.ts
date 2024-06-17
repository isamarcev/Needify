import { AddUserWalletParams, EditUserParams } from '@/services/types';

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

export async function editUser(id: number, params: EditUserParams) {
  const res = await fetch(`${BASE_URL}/v1/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error('Failed to get users');
  }

  return res.json();
}

export async function addUserWallet(params: AddUserWalletParams) {
  const res = await fetch(
    `${BASE_URL}/v1/users/wallet/add?telegram_id=${params.telegramId}`,
    {
      method: 'POST',
      body: {
        address: params.address,
      },
    },
  );

  if (!res.ok) {
    throw new Error('Failed to add user wallet');
  }

  return res.json();
}

// Currency

// Task
export async function getTasks() {
  const res = await fetch(`${BASE_URL}/v1/task`);

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
export async function getCategories() {
  const res = await fetch(`${BASE_URL}/v1/category`);

  if (!res.ok) {
    throw new Error('Failed to get tasks');
  }

  return res.json();
}
// Ton-connect
