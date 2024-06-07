import dotenv from 'dotenv'; 
dotenv.config()
import { Address, internal, fromNano, beginCell, toNano, SendMode } from '@ton/core';
import { TokenMaster, storeDeploy, storeMint } from '../wrappers/TokenMaster';
import { NetworkProvider } from '@ton/blueprint';
import { buildOnchainMetadata } from "../utils/jetton-helpers";

import { content } from "./deployMaster"

import { mnemonicToPrivateKey } from "ton-crypto";
import { WalletContractV4 } from '@ton/ton';
import { storeTransfer } from '../wrappers/JobOffer';
import { log } from 'console';


const deploy_mnemonics_array = process.env.DEPLOYER_MNEMONIC || "";
const mnemonic = deploy_mnemonics_array?.split(" ");


export async function run(provider: NetworkProvider) {
    let client = provider
    let keyPair = await mnemonicToPrivateKey(mnemonic);
    let secretKey = keyPair.secretKey;
    let workchain = 0;
    let deployer_wallet = WalletContractV4.create({
        workchain,
        publicKey: keyPair.publicKey,
    });
    let wallet_contract = client.open(deployer_wallet);
    const master = client.open(await TokenMaster.fromInit(
        deployer_wallet.address, content
    ));
    let destination_address = Address.parse("EQB95rI40tmkhT4OLyfrRZZcAbJb6Ys5-xCQRCh_ol0Z2nX6")
    // let destination_address = deployer_wallet.address

    let seqno: number = await wallet_contract.getSeqno();
    let balance: bigint = await wallet_contract.getBalance();
    // ========================================
    console.log("Current deployment wallet balance: ", fromNano(balance).toString(), "💎TON");
    console.log("\n🛠️ Calling To JettonWallet:\n" + master.address + "\n");
    let transferMessagePkg = beginCell().store(
        storeTransfer({
            $$type: "Transfer",
            query_id: 1n,
            amount: toNano(1000000),
            destination: destination_address,
            response_destination: destination_address,
            custom_payload: beginCell().endCell(),
            forward_ton_amount: toNano(0.4),
            forward_payload: beginCell().endCell(),
        })
        )
        .endCell()
    let simple_mint = beginCell().store(
        storeMint({
            $$type: "Mint",
            amount: toNano(10000),
            receiver: destination_address,
        })
    ).endCell()
    let transfer = wallet_contract.createTransfer({
        seqno,
        secretKey: secretKey,
        sendMode: SendMode.IGNORE_ERRORS,
        messages: [internal({
            to: master.address,
            value: "0.65",
            body: simple_mint,
        })],
        
    });

    // Perform transfer
    await wallet_contract.send(transfer);
}
