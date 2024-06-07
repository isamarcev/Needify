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
    let destination_address = Address.parse("kQAih7EZXVVLQTazIB0BHiapgLNIybWmTCVq8nXVlv0cauBI")
    // let destination_address = deployer_wallet.address

    let seqno: number = await wallet_contract.getSeqno();
    let balance: bigint = await wallet_contract.getBalance();
    // ========================================
    console.log("Current deployment wallet balance: ", fromNano(balance).toString(), "💎TON");
    console.log("\n🛠️ Calling To JettonWallet:\n" + master.address + "\n");
    let cell = wallet_contract.createTransfer({
        seqno,
        secretKey: secretKey,
        sendMode: SendMode.IGNORE_ERRORS,
        messages: [
            internal({
                to: destination_address,
                value: toNano(0.1),
                bounce: false
            })
        ],
    }
    )
    let transfer = await wallet_contract.send(cell);

    // Perform transfer
}
