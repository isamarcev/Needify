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
    name: "TRUE",
    description: "This is True description",
    symbol: "TRUE",
    image: "https://play-lh.googleusercontent.com/ahJtMe0vfOlAu1XJVQ6rcaGrQBgtrEZQefHy7SXB7jpijKhu1Kkox90XDuH8RmcBOXNn",
};
export let content = buildOnchainMetadata(jettonParams);

const NativejettonParams = {
    name: "The Open Needs",
    description: "This is True description",
    symbol: "NEED",
    image: "https://play-lh.googleusercontent.com/ahJtMe0vfOlAu1XJVQ6rcaGrQBgtrEZQefHy7SXB7jpijKhu1Kkox90XDuH8RmcBOXNn",
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

    let seqno: number = await wallet_contract.getSeqno();
    let balance: bigint = await wallet_contract.getBalance();
    // ========================================
    console.log("Current deployment wallet balance: ", fromNano(balance).toString(), "💎TON");
    console.log("\n🛠️ Calling To JettonWallet:\n" + master.address + "\n");

    let transferMessagePkg = beginCell().store(
        storeTransfer({
            $$type: "Transfer",
            query_id: 1n,
            amount: toNano(199),
            destination: deployer_wallet.address,
            response_destination: deployer_wallet.address,
            custom_payload: beginCell().endCell(),
            forward_ton_amount: toNano(0.4),
            forward_payload: beginCell().endCell(),
        })
        )
        .endCell()
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
        })],
        
    });

    // Perform transfer
    await wallet_contract.send(transfer);
}
