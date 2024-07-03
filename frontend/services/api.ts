import {
  AddUserWalletParams,
  EditUserParams,
  ETaskStatus,
  ICategoryRaw,
  ITaskRaw,
  CreateTaskParams,
  CreateUserParams,
  getMessageParams,
  getConfirmMessageParams,
  getChooseDoerMessageParams
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
  try {
    const res = await fetch(`${BASE_URL}/v1/users/${id}`);
    return res.json();
  } catch (error) {
    return {};
  }


  

}

export async function createUser(params: CreateUserParams) {
  const res = await fetch(`${BASE_URL}/v1/users`, {
    method: 'POST',
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

export async function getUserTasks(id: number) {

  const res = await fetch(`${BASE_URL}/v1/task/${id}/tasks`);

  if (!res.ok) {
    throw new Error('Failed to get tasks');
  }

  return res.json();
}

export async function createTask(params: CreateTaskParams) {
  const res = await fetch(`${BASE_URL}/v1/task`, {
    method: 'POST',
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error('Failed to create task');
  }

  return res.json();
}

// Job-offer
export async function getDeployMessage(params: getMessageParams) {
  const res = await fetch(`${BASE_URL}/v1/job-offer/message/deploy`, {
    method: 'POST',
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error('Failed to get categories');
  }

  return res.json();
}

export async function getRevokeMessage(params: getMessageParams) {
  const res = await fetch(`${BASE_URL}/v1/job-offer/message/revoke`, {
    method: 'POST',
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error('Failed to get categories');
  }

  return res.json();
}

export async function getCompleteMessage(params: getMessageParams) {
  const res = await fetch(`${BASE_URL}/v1/job-offer/message/complete`, {
    method: 'POST',
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error('Failed to get categories');
  }

  return res.json();
}

export async function getConfirmMessage(params: getConfirmMessageParams) {
  const res = await fetch(`${BASE_URL}/v1/job-offer/message/confirm`, {
    method: 'POST',
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error('Failed to get categories');
  }

  return res.json();
}

export async function getGetJobMessage(params: getMessageParams) {
  const res = await fetch(`${BASE_URL}/v1/job-offer/message/get-job`, {
    method: 'POST',
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error('Failed to get categories');
  }

  return res.json();
}

export async function getChooseDoerMessage(params: getChooseDoerMessageParams) {
  const res = await fetch(`${BASE_URL}/v1/job-offer/message/choose-doer`, {
    method: 'POST',
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    throw new Error('Failed to get categories');
  }

  return res.json();
}

// Category
export async function getCategories(): Promise<ICategoryRaw[]> {
  const res = await fetch(`${BASE_URL}/v1/category`);

  if (!res.ok) {
    throw new Error('Failed to get categories');
  }

  return res.json();
}

// Ton-connect
