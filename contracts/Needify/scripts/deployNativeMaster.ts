import dotenv from 'dotenv'; 
dotenv.config()
import { beginCell, fromNano, internal, toNano } from '@ton/core';
import { NativeMaster, storeMint } from '../wrappers/NativeMaster';
import { NetworkProvider } from '@ton/blueprint';
import { buildOnchainMetadata } from "../utils/jetton-helpers";


import { mnemonicToPrivateKey } from "ton-crypto";
import { WalletContractV4 } from '@ton/ton';
import { storeTransfer } from '../wrappers/JobOffer';
import { log } from 'console';

const NativejettonParams = {
    name: "Needify",
    description: "NEED is a token for the Needify platform. It is used to pay for services and goods on the platform.",
    symbol: "NEED",
    image: "https://i.ibb.co/Bf38Vcp/Needify-logo.png",
};
const native_decimals = 9n;

function toTokenNano(value: bigint) {
    return value * 10n ** native_decimals;
}

export let native_content = buildOnchainMetadata(NativejettonParams);
const deploy_mnemonics_array = process.env.DEPLOYER_MNEMONIC || "";
const mnemonic = deploy_mnemonics_array?.split(" ");
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
    const master = client.open(await NativeMaster.fromInit(
        deployer_wallet.address, native_content
    ))
    
    let seqno: number = await wallet_contract.getSeqno();
    let balance: bigint = await wallet_contract.getBalance();
    // ========================================
    console.log("Current deployment wallet balance: ", fromNano(balance).toString(), "💎TON");
    console.log("\n🛠️ Calling To JettonWallet:\n" + master.address + "\n");

    let ming_message = beginCell().store(
        storeMint({
            amount: toTokenNano(100_000n),
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
        ],
        
    });

    // Perform transfer
    await wallet_contract.send(transfer);
}
