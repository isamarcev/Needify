import { Blockchain, SandboxContract, TreasuryContract } from '@ton/sandbox';
import { Address, OpenedContract, toNano } from '@ton/core';
import { TokenWallet } from '../wrappers/TokenWallet';
import '@ton/test-utils';
import { JobOffer } from '../build/TokenMaster/tact_JobOffer';
import { TonClient4, WalletContractV4 } from '@ton/ton';
import { TokenMaster } from '../wrappers/TokenMaster';
import { KeyPair, mnemonicToPrivateKey } from 'ton-crypto';


const jetton_master_deployer = process.env.DEPLOYER_MNEMONIC || "";
const jetton_master_deployer_mnem = jetton_master_deployer?.split(" ");
const poster_mnemonic_str = process.env.POSTER_MNEMONIC || "";
const poster_mnemonic = poster_mnemonic_str?.split(" ");


describe('TokenWallet', () => {
    let jobOffer: SandboxContract<JobOffer>;

    let client: TonClient4
    let JOInitAddress: Address
    let master: OpenedContract<TokenMaster>
    let deployer_wallet: OpenedContract<WalletContractV4>
    let keyPairDeployer: KeyPair
    
    beforeEach(async () => {

        // client = new TonClient4({ endpoint: 'https://testnet-v4.tonhubapi.com' })
        // let workchain = 0;

        // deployer section
        // keyPairDeployer = await mnemonicToPrivateKey(jetton_master_deployer_mnem);
        // let secretKeyDeployer = keyPairDeployer.secretKey;
        // let deployer_contractV4 = WalletContractV4.create({
        //     workchain,
        //     publicKey: keyPairDeployer.publicKey,
        // });
        // deployer_wallet = client.open(deployer_contractV4);

        // Jetton Master
        // master = client.open(await TokenMaster.fromInit(
        //     // deployer_contractV4.address, content
        // ));

        // log(fromNano(await deployer_wallet.getBalance()))
        // log(fromNano((await master.getGetJettonData()).total_supply))
        // sleep(1000 * 10)

        // Poster section
        // let keyPairPoster = await mnemonicToPrivateKey(poster_mnemonic);
        // let secretKeyPoster = keyPairPoster.secretKey;
        // let poster_contractV4 = WalletContractV4.create({
        //     workchain,
        //     publicKey: keyPairPoster.publicKey,
        // });
        // let poster_wallet_contract = client.open(poster_contractV4);


        // JOB OFFER CREATION
        // let JOInit = await JobOffer.init(
        //     title, description, price, order, master.address
        // )    
        // JOInitAddress = contractAddress(workchain, JOInit);
        // log("Job offer address: ", JOInitAddress)
        // let seqno: number = await poster_wallet_contract.getSeqno();
        // let balance: bigint = await poster_wallet_contract.getBalance();

        // // DEPLOY JOB OFFER
        // let deploy_msg = beginCell().store(storeDeploy({
        //     $$type: "Deploy",
        //     queryId: 1n,
        // })).endCell();
        // log("Current deployment wallet balance = ", fromNano(balance).toString(), "💎TON");
        // log("Deployer address = ", poster_wallet_contract.address);

        // DEPLOY 
        // let JO = client.open(await JobOffer.fromInit(
        //     title, description, price, order, master.address
        // ))
        // let s = (await JO.getJobData())
        // await poster_wallet_contract.sendTransfer({
        //         seqno,
        //         secretKey: secretKeyPoster,
        //         sendMode: SendMode.IGNORE_ERRORS,
        //         messages: [
        //             internal({
        //                 to: JOInitAddress,
        //                 value: toNano("0.5"),
        //                 init: {
        //                     code: JOInit.code,
        //                     data: JOInit.data,
        //                 },
        //                 body: deploy_msg,
        //             }),
        //         ],
        //     });
        // // WITHDRAW TEST
        // seqno = await poster_wallet_contract.getSeqno();
        // let withdraw_message = beginCell().store(
        //     storeWithdraw({
        //         $$type: "Withdraw",
        //         to: poster_wallet_contract.address,
        //         amount: toNano(10000)
        //     })
        // ).endCell()
        // await poster_wallet_contract.sendTransfer({
        //     seqno,
        //     secretKey: secretKeyPoster,
        //     sendMode: SendMode.IGNORE_ERRORS,
        //     messages: [
        //         internal({
        //             to: JOInitAddress,
        //             value: toNano("1"),
        //             body: withdraw_message,
        //         }),
        //     ],
        // });

        // test restart
        // seqno = await poster_wallet_contract.getSeqno();
        // let restart_message = "restart"
        // await poster_wallet_contract.sendTransfer({
        //     seqno,
        //     secretKey: secretKeyPoster,
        //     sendMode: SendMode.IGNORE_ERRORS,
        //     messages: [
        //         internal({
        //             to: JOInitAddress,
        //             value: toNano("0.01"),
        //             body: restart_message,
        //         }),
        //     ],
        // });
        


    });
    
    // let blockchain: Blockchain;
    // let deployer: SandboxContract<TreasuryContract>;
    // let tokenWallet: SandboxContract<TokenWallet>;

    // beforeEach(async () => {
    //     blockchain = await Blockchain.create();

    //     tokenWallet = blockchain.openContract(await TokenWallet.fromInit());

    //     deployer = await blockchain.treasury('deployer');

    //     const deployResult = await tokenWallet.send(
    //         deployer.getSender(),
    //         {
    //             value: toNano('0.05'),
    //         },
    //         {
    //             $$type: 'Deploy',
    //             queryId: 0n,
    //         }
    //     );

    //     expect(deployResult.transactions).toHaveTransaction({
    //         from: deployer.address,
    //         to: tokenWallet.address,
    //         deploy: true,
    //         success: true,
    //     });
    // });

    it('should deploy', async () => {
        // the check is done inside beforeEach
        // blockchain and tokenWallet are ready to use
    });
});
