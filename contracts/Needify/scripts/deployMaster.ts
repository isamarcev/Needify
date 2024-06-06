import dotenv from 'dotenv'; 
dotenv.config()
import { Address, internal, fromNano, beginCell, toNano } from '@ton/core';
import { TokenMaster, storeDeploy, storeMint } from '../build/TokenMaster/tact_TokenMaster';

import { NetworkProvider } from '@ton/blueprint';
import { buildOnchainMetadata } from "../utils/jetton-helpers";



import { mnemonicToPrivateKey } from "ton-crypto";
import { WalletContractV4 } from '@ton/ton';
import { storeTransfer } from '../wrappers/JobOffer';
import { log } from 'console';

const jettonParams = {
    name: "THE TEST USDT",
    description: "This is True description",
    symbol: "TUSDT",
    image: "https://ibb.co/8YFKv25",
    decimals: "6",
};
export let content = buildOnchainMetadata(jettonParams);

const NativejettonParams = {
    name: "Needify",
    description: "NEED is a token for the Needify platform. It is used to pay for services and goods on the platform.",
    symbol: "NEED",
    image: "https://ibb.co/sVz9Tp7",
};
export let native_content = buildOnchainMetadata(NativejettonParams);

const deploy_mnemonics_array = process.env.DEPLOYER_MNEMONIC || "";
const mnemonic = deploy_mnemonics_array?.split(" ");

const poster_mnemonics_array = process.env.POSTER_MNEMONIC || "";
const poster_mnemonic = poster_mnemonics_array?.split(" ");

export async function run(provider: NetworkProvider) {
    let client = provider
    
    let DeloyerkeyPair = await mnemonicToPrivateKey(mnemonic);
    let secretKey = DeloyerkeyPair.secretKey;
    let workchain = 0;
    let deployer_wallet = WalletContractV4.create({
        workchain,
        publicKey: DeloyerkeyPair.publicKey,
    });
    let wallet_contract = client.open(deployer_wallet);
    const master = client.open(await TokenMaster.fromInit(
        deployer_wallet.address, content
    ))

    const native_master = client.open(await TokenMaster.fromInit(
        deployer_wallet.address, native_content
    ))

    let seqno: number = await wallet_contract.getSeqno();
    let balance: bigint = await wallet_contract.getBalance();
    // ========================================
    console.log("Current deployment wallet balance: ", fromNano(balance).toString(), "💎TON");
    console.log("\n🛠️ Calling To JettonWallet:\n" + master.address + "\n");

    let ming_message = beginCell().store(
        storeMint({
            amount: toNano(1000),
            receiver: deployer_wallet.address,
            $$type: "Mint"
        })
    ).endCell()
    let transfer = wallet_contract.createTransfer({
        seqno,
        secretKey: secretKey,
        messages: [internal({
            to: master.address,
            value: "0.65",
            body: ming_message,
            bounce: false,
            init: {
                data: master.init?.data,
                code: master.init?.code
            }
        }),
            internal({
                to: native_master.address,
                value: "0.65",
                body: ming_message,
                bounce: false,
                init: {
                    data: native_master.init?.data,
                    code: native_master.init?.code
                }
            })
        ],
        
    });

    // Perform transfer
    await wallet_contract.send(transfer);
}
